///////////////////////////////////
//Coded by Rajandran R
//Date : 05th July 2015
///////////////////////////////////

_SECTION_BEGIN("Rotational Factor - Market Profile");


RF = 0;
NewDay = day() != Ref(day(), -1);

for(i=1;i<BarCount;i++)
{
if(NewDay==True)
{
BarsUp=0;
BarsDown=0;
RF = 0;

}
//If Current Bar Makes HH and HL
if(H>H[i-1] AND L>L[i-1] AND !NewDay)
{
RF=RF[i-1]+2;
}

//If Current Bar Makes LH and LL
if(H<H[i-1] AND L<L[i-1] AND !NewDay)
{
RF=RF[i-1]-2;
}

//If Current Bar Makes HH and LL
if(H>H[i-1] AND L<L[i-1] AND !NewDay)
{
RF=RF[i-1];
}

//If Current Bar Makes LH and HL
if(H<H[i-1] AND L>L[i-1] AND !NewDay)
{
RF[i]=RF[i-1];
}

if(H[i]==H[i-1] AND L[i]>L[i-1] AND !NewDay[i])
{
RF[i]=RF[i-1]+1;
}

if(H[i]>H[i-1] AND L[i]==L[i-1] AND !NewDay[i])
{
RF[i]=RF[i-1]+1;
}

if(H[i]<H[i-1] AND L[i]==L[i-1] AND !NewDay[i])
{
RF[i]=RF[i-1]-1;
}

if(H[i]==H[i-1] AND L[i]<L[i-1] AND !NewDay[i])
{
RF[i]=RF[i-1]-1;
}

}

Plot(0,"",colorIndigo,styleline);

Plot(RF,"Rotational Factor", IIf(RF>0,colorGreen,colorRed),styleHistogram | stylethick);

_SECTION_END();
[/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i][/i]